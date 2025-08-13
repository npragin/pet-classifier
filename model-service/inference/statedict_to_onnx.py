import torch
from train.models.convnext import ConvNext


def main():
    checkpoint = torch.load("train/chkpts/EOIbVK_CIFAR10_epoch141")
    state_dict = checkpoint["state_dict"]
    blocks = checkpoint["blocks"]

    model = ConvNext(3, 37, blocks=blocks)
    model.load_state_dict(state_dict)

    dummy_input = torch.randn(1, 3, 224, 224)

    onnx_program = torch.onnx.export(
        model,
        dummy_input,
        dynamo=True,
        input_names=["input"],
        output_names=["output"],
        dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}},
    )
    onnx_program.optimize()

    onnx_program.save("breed_classifier.onnx")


if __name__ == "__main__":
    main()
