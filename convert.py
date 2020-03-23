import numpy as np
import torch
import tools

def save_weight_to_darknet(weight_path: str, save_path: str, seen: int=0):
    fw = open(save_path, 'wb')

    state_dict = torch.load(weight_path, map_location=torch.device('cpu'))['model']

    header = np.array([0, 0, 0, seen], dtype=np.int32)
    header.tofile(fw)

    pre_conv = None
    pre_bias = []
    for key, params in state_dict.items():
        params_shape = len(params.shape)
        if params_shape == 4: # conv weight
            if pre_conv is not None:
                pre_conv.numpy().tofile(fw)
            pre_conv = params
        elif params_shape == 1: #BN or conv_bias
            if key.endswith('bias') and len(pre_bias) == 0: # conv_bias
                params.numpy().tofile(fw)
                pre_conv.numpy().tofile(fw)
                pre_conv = None
            else: # BN
                pre_bias.append(params)
                if len(pre_bias) == 4:
                    pre_bias[1].numpy().tofile(fw)
                    pre_bias[0].numpy().tofile(fw)
                    pre_bias[2].numpy().tofile(fw)
                    pre_bias[3].numpy().tofile(fw)
                    pre_bias.clear()
                    assert pre_conv is not None
                    pre_conv.numpy().tofile(fw)
                    pre_conv = None
        else:
            pass

    if pre_conv is not None:
        pre_conv.numpy().tofile(fw)

    fw.close()

def export_quant_to_onnx(cfg_path: str, weight_path: str):
    model = tools.build_model(
        cfg_path, weight_path, device='cpu', dataparallel=False, quantized=True, backend='qnnpack'
    )[0]
    model.eval()
    # print(model)

    torch_in = torch.randn(1, 3, 512, 512)
    dynamic_axes = {'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
    torch.onnx.export(
        model, torch_in, 'export/quant_myolo.onnx', verbose=True, input_names=['input'],
        output_names=['output'], dynamic_axes=dynamic_axes, opset_version=9,
        operator_export_type=torch.onnx.OperatorExportTypes.ONNX_ATEN_FALLBACK
    )

def export_normal_to_onnx(cfg_path: str, weight_path: str):
    model = tools.build_model(
        cfg_path, weight_path, device='cpu', dataparallel=False
    )[0]
    model.eval()

    torch_in = torch.randn(1, 3, 512, 512)
    dynamic_axes = {'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
    torch.onnx.export(
        model, torch_in, 'export/myolo.onnx', verbose=False, input_names=['input'],
        output_names=['output'], dynamic_axes=dynamic_axes, opset_version=11,
    )

if __name__ == "__main__":
    weight_path = 'weights/VOC_quant3/model-44.pt'
    # weight_path = 'weights/trained/model-74-0.7724.pt'
    # save_weight_to_darknet(weight_path, weight_path.rsplit('.', 1)[0]+'-convert.weights')
    export_quant_to_onnx('model/cfg/mobilenetv2-yolo.cfg', weight_path)
    # export_normal_to_onnx('model/cfg/mobilenetv2-yolo.cfg', weight_path)
