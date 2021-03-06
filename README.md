# PQDet

## Introduction

This repo mainly refers to Stronger-yolov3 and Stronger-yolo-pytorch as well as other lastest parpers.

This repo is implemented using PyTorch.

This repo is under development.

## Installation

Python >= 3.6, install packages by `pip install -r requirements.txt`.

Packages about onnx and imagesize, torchsummaryX and pyclustering is optional.

## Datasets

We current support VOC, COCO and Visdrone dataset.

For VOC dataset, follow [here][1] to download file and unzip it, then put `dataset/scripts/voc_txt.py` in `Pascal_voc` directory and run it to generate txt file.

For COCO dataset, follow [here][1].

For Visdrone dataset, download Task 1 [dataset][2] and unzip it, then use `dataset/scripts/visdrone_txt.py` in unzipped directory.

For custom dataset, you need to create 2 txt file including image path per line. One for training, one for eval. Then make a new `dataset_name_sample.py` file in `dataset` like `voc_sample.py`. Where you parse label, pre/post-process, augment, etc. After that, register them in `dataset/__init__.py`.

## Train

Adapt your setting yaml file based on file in `yamls/`. You may need to change `experiment_name`, `dataset.name`, `train_txt_file`, `learning_rate_init`, etc. See `config.py` for all settings and their meanings.

Note: You need to scale `learning_rate_init` by number of GPUs. By default, it is 2e-4 x NUM_OF_GPUS.

Dowload imagenet pretrained weights: [Baidu Yun (pw: hnr5)](https://pan.baidu.com/s/11NwfFvKZD36wzXX4uTUbGA) and [Google drive](https://drive.google.com/drive/folders/1xsSEw-realVaCYQXnngsBrmeyouKcdRp?usp=sharing). Put them in `weights/pretrained/`.

Train you model by `python trainer.py --yaml dataset.yaml`.

## Eval

For example:
```
python test.py eval --yaml yamls/voc.yaml --cfg model/cfg/mobilenetv2-fpn.cfg --weight weights/voc_mobilenetv2_fpn_l1_baseline/model-58-0.4790.pt --bs 80
```
See `test.py` for more information.

## Predict

For example:
```
python predict.py --yaml yamls/visdrone.yaml --dataset visdrone --cfg model/cfg/regnetx-600m-fpn-visdrone.cfg --weight weights/VisDrone/model-29-0.1648.pt --img data/images/0000142_04458_d_0000045.jpg --threshold 0.3
```

## Prune

We implement channel-prune method according [slimming][3]. And only support vanilla conv or deepwise conv now.

First, turn on sparse train in yaml file and train. By default, we use 0.01 sparse ratio. You may need to use longer scheduler or larger sparse ratio if bn's gama is large.

After sparse train, prune and fine-tune. For example:
```
python prune.py --yaml yamls/voc.yaml
```

## Quantization Aware Training(QAT)

Turn on quant.switch in yaml file.

Set `disable_observer_after` and `freeze_bn_after` properly.
If you train from scratch, set former 0.1x max epochs, latter 2-4 larger than former.
These are based on experience, try yourself.

You can also fine-tune from a trained model. That will save a lot of time.

Currently we don't use multi GPUs in QAT in pytorch, see [this issue][4].
So you need to reduce batch size and learning rate. QAT is much slower and consume more memory than normal training.

## Export to ONNX

See `convert.py` for more info.

We support exporting quantized model, see `export/onnx_exporter.py`.

## Custom network architecture

For now we implement MobileNetV2, RegnetX-600M and RegnetY-400M backbone.

We basically implement a darknet cfg parser. Most of them have the same behavior.
You can write cfg file by yourself and add more op. See files in `model/`.

## NAS

This part is experimental, not good so far.

## Model Zoo

### VOC 07+12

All models use imagenet pretrained backbone, trained on VOC 07+12 trainval set, and evaluate on VOC 07 test set.

Image input size is 512x512. The evaluate code refers to cocoeval, may be ~1% higher than VOC evaluator.

| model name           | AP   | AP50 | AP75 | MACs   | params | forward time (bs=1/4/16) | train time (per epoch) | GPU            | train batch size (per GPU) | train epochs | learn rate |
|----------------------|------|------|------|--------|--------|--------------------------|------------------------|----------------|----------------------------|--------------|------------|
| mobilenetv2-fpn.cfg  | 48.1 | 81.5 | 50.7 | 4.336G | 6.775M | 11.5/22.6/84.3ms         | 187s                   | 2x GTX 1080 Ti | 16                         | 60           | 4e-4       |
| regnetx-600m-fpn.cfg | 48.6 | 81.6 | 51.4 | 4.387G | 7.417M | 15.9/16.5/50.9ms         | 163s                   | 2x GTX 1080 Ti | 16                         | 60           | 4e-4       |
| regnetx-600m-pan.cfg | 48.1 | 80.9 | 51.1 | 4.210G | 7.145M | 14.4/15.2/47.9ms         | 152s                   | 2x GTX 1080 Ti | 16                         | 60           | 4e-4       |
| regnety-400m-fpn.cfg | 48.2 | 82.2 | 50.8 | 3.324G | 5.581M | 22.9/23.3/55.6ms         | 192s                   | 2x GTX 1080 Ti | 16                         | 60           | 4e-4       |

[1]: https://github.com/AlexeyAB/darknet#datasets
[2]: https://github.com/VisDrone/VisDrone-Dataset
[3]: http://openaccess.thecvf.com/content_ICCV_2017/papers/Liu_Learning_Efficient_Convolutional_ICCV_2017_paper.pdf
[4]: https://github.com/pytorch/pytorch/issues/35182