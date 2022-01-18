from typing import Any, Mapping

import flax.linen as nn
import jax
import jax.numpy as jnp
import numpy as np
import optax
from clu import metric_writers
from flax.training import train_state
from torch.utils.data import DataLoader
from tqdm import tqdm

Scalars = Mapping[str, jnp.ndarray]


class TrainState(train_state.TrainState):
    batch_stats: Any = None


def create_train_state(
    rng: int,
    net: nn.Module,
    batch_shape: jnp.ndarray,
    optimizer: optax.GradientTransformation,
) -> TrainState:
    """Creates initial `TrainState`
    Args:
        rng (int): Seed for PRNG key for parameter initialization.
        net (nn.Module): Network to train.
        batch_shape (jnp.ndarray): Shape of batched inputs e.g. [B, C, H, W].
        optimizer (optax.GradientTransformation): Optax optimizer to use.
    Returns:
        TrainState: Flax class for storing training state and useful methods.
    """
    rng = jax.random.PRNGKey(rng)
    dummy_input = jnp.ones(batch_shape, dtype=net.dtype)
    jit_init = jax.jit(net.init)
    variables = jit_init({"params": rng}, dummy_input)
    params = variables["params"]
    batch_stats = variables["batch_stats"]
    return TrainState.create(
        apply_fn=net.apply, params=params, tx=optimizer, batch_stats=batch_stats
    )


def cross_entropy_loss(logits, labels):
    one_hot_labels = jax.nn.one_hot(labels, num_classes=10)
    xentropy = optax.softmax_cross_entropy(logits=logits, labels=one_hot_labels)
    return jnp.mean(xentropy)


def compute_metrics(
    logits: jnp.ndarray,
    labels: jnp.ndarray,
) -> Scalars:
    loss = cross_entropy_loss(logits, labels)
    accuracy = jnp.mean(jnp.argmax(logits, -1) == labels)
    metrics = {
        "loss": loss,
        "accuracy": accuracy,
    }
    return metrics


@jax.jit
def train_step(state, batch):
    imgs, labels = batch

    def loss_fn(params):
        """loss function used for training."""
        variables = {"params": params, "batch_stats": state.batch_stats}
        logits, new_model_state = state.apply_fn(
            variables,
            imgs,
            mutable=["batch_stats"],
        )
        loss = cross_entropy_loss(logits, labels)
        return loss, (new_model_state, logits)

    grad_fn = jax.value_and_grad(loss_fn, has_aux=True)
    aux, grads = grad_fn(state.params)
    new_model_state, logits = aux[1]
    new_state = state.apply_gradients(
        grads=grads, batch_stats=new_model_state["batch_stats"]
    )
    metrics = compute_metrics(logits, labels)
    return new_state, metrics


@jax.jit
def val_step(state, batch):
    imgs, labels = batch
    variables = {"params": state.params, "batch_stats": state.batch_stats}
    logits = state.apply_fn(variables, imgs, train=False, mutable=False)
    return compute_metrics(logits, labels)


@jax.jit
def test_step(state, batch):
    imgs = batch
    variables = {"params": state.params, "batch_stats": state.batch_stats}
    logits = state.apply_fn(variables, imgs, train=False, mutable=False)
    preds = jnp.argmax(logits, -1)
    return imgs, preds


def train_digit_classifier(
    rng: int,
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    num_epochs: int,
    optimizer: optax.GradientTransformation,
    logger: metric_writers.MetricWriter = None,
    log_every_n_steps: int = 100,
):
    """Trains the digit classifier.

    Args:
        rng (int): Seed for PRNG key for parameter initialization.
        model (nn.Module): Flax Network to train.
        train_loader (DataLoader): Pytorch DataLoader for training data.
        val_loader (DataLoader): Pytorch DataLoader for validation data.
        num_epochs (int): Number of epochs to train for.
        optimizer (optax.GradientTransformation): Optax optimizer to use.
        logger (SummaryWriter, optional): CLU logger to use. Defaults to None.
        log_every_n_steps (int, optional): How often to log to TB. Defaults to 100.

    Returns:
        TrainState: Final state of the network.
    """
    min_loader_len = min(len(train_loader), len(val_loader))
    assert log_every_n_steps < min_loader_len or logger is None, (
        "log_every_n_steps must be less than the length of the dataloader, got"
        f" {log_every_n_steps=} >= {min_loader_len=}"
    )

    imgs, *_ = next(iter(train_loader))  # dummy batch for init
    batch_shape = imgs.shape
    state = create_train_state(rng, model, batch_shape, optimizer)

    for epoch in range(num_epochs):
        for mode in ["train", "val"]:
            loader = train_loader if mode == "train" else val_loader

            global_step = epoch * len(loader)
            total_accuracy = 0.0
            total_loss = 0.0

            for step, batch in enumerate(
                tqdm(loader, total=len(loader), desc=f"Epoch {epoch}, {mode}")
            ):
                if mode == "train":
                    state, metrics = train_step(state, batch)
                else:
                    metrics = val_step(state, batch)

                total_accuracy += metrics["accuracy"]
                total_loss += metrics["loss"]

                if logger is not None and (step + 1) % log_every_n_steps == 0:
                    logger.write_scalars(
                        global_step + step,
                        {
                            f"{mode}/loss": total_loss / log_every_n_steps,
                            f"{mode}/accuracy": total_accuracy / log_every_n_steps,
                        },
                    )
                    total_loss = 0
                    total_accuracy = 0
                logger.flush()
    return state


def test_digit_classifier(state: TrainState, test_loader: DataLoader):
    """Generate an array of predictions for the test set.

    Args:
        state (TrainState): State of the network.
        test_loader (DataLoader): Pytorch DataLoader for test data.

    Returns:
        np.ndarray: Array of predictions for the test set.
    """

    preds = []
    imgs = []

    for batch in tqdm(
        test_loader, total=len(test_loader), desc="Generating Predictions on Test Set"
    ):
        batch_imgs, batch_preds = test_step(state, batch)
        preds.append(batch_preds)
        imgs.append(batch_imgs)

    final_preds = np.array(jnp.concatenate(preds, axis=0))
    final_imgs = np.array(jnp.concatenate(imgs, axis=0))
    return final_imgs, final_preds
