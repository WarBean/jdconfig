# Extended Python dict for flexible hyperparameter configuration in Deep Learning

## **Code has been updated to v2.0. Documentation is comming soon. **

## Installation

```shell
# Either
pip install jdconfig
# Or
pip install --upgrade https://github.com/WarBean/jdconfig/tarball/master
```

## Usage

### 1.Basic Loading

Suppose you have a json file `hyperparameter.json` containing your DL hyperparameters:

```json
{
    "dataset": {
        "proc_count": 4,
        "batch_size": 32,
        "image_height": 48,
        "image_width": 1024
    },

    "model": {
        "cnn_channel":  [   128,    128,    256,    256,    256],
        "cnn_kernel" :  [[4, 4], [3, 3], [3, 3], [3, 3], [3, 2]],
        "cnn_stride" :  [[2, 1], [1, 1], [2, 2], [1, 1], [2, 2]],
        "cnn_padding":  [[0, 0], [1, 1], [0, 0], [1, 1], [0, 0]],
        "dropout": 0.05
    },

    "init": {
        "name": "normal",
        "args": { "std": 1 }
    },

    "optim": {
        "name": "Adam",
        "args": {
            "lr": 1e-3,
            "betas": [0.9, 0.99]
        },
        "lr_decay_point": [1000, 2000],
        "clip_grad": null
    },

    "train_iter_count": 100000,
    "report_interval": 10,
    "valid_interval": 10,
    "visualize_interval": 500,
    "visualize_count": 5,
    "save_interval": 1000
}

```

Use `jdconfig.Config` to load the configuration:

```python
from jdconfig import Config
config = Config('hyperparameter.json')
print(config.train_iter_count)
print(config.model.dropout)
print(config.model.cnn_channel) 
```

Output:
```shell
100000
0.05
[128, 128, 256, 256, 256]
```

### 2.Passing Around

After that you can pass around the `config` object to wherever it is needed. For example, when I'm using PyTorch to create a network module:

```python
import torch
from jdconfig import Config

class MyCNN(torch.nn.Sequential):
    def __init__(self, config):
        super(MyCNN, self).__init__()
        num_conv = len(config.model.cnn_channel)
        in_channel = 3
        for i in range(num_conv):
            conv = torch.nn.Conv2d(
                in_channel,
                config.model.cnn_channel[i],
                config.model.cnn_kernel[i],
                config.model.cnn_stride[i],
                config.model.cnn_padding[i]
            )
            self.add_module('conv%d' % i, conv)
            dropout = torch.nn.Dropout(config.model.dropout)
            self.add_module('dropout%d' % i, dropout)
            relu = torch.nn.ReLU()
            self.add_module('relu%d' % i, relu)
config = Config('hyperparameter.json')
my_cnn = MyCNN(config)
print(my_cnn)
```

Output:

```shell
MyCNN (
  (conv0): Conv2d(3, 128, kernel_size=[4, 4], stride=[2, 1], padding=[0, 0])
  (dropout0): Dropout (p = 0.05)
  (relu0): ReLU ()
  (conv1): Conv2d(3, 128, kernel_size=[3, 3], stride=[1, 1], padding=[1, 1])
  (dropout1): Dropout (p = 0.05)
  (relu1): ReLU ()
  (conv2): Conv2d(3, 256, kernel_size=[3, 3], stride=[2, 2], padding=[0, 0])
  (dropout2): Dropout (p = 0.05)
  (relu2): ReLU ()
  (conv3): Conv2d(3, 256, kernel_size=[3, 3], stride=[1, 1], padding=[1, 1])
  (dropout3): Dropout (p = 0.05)
  (relu3): ReLU ()
  (conv4): Conv2d(3, 256, kernel_size=[3, 2], stride=[2, 2], padding=[0, 0])
  (dropout4): Dropout (p = 0.05)
  (relu4): ReLU ()
)
```

### 3.Modification on the fly

`jdconfig.Config` object is not just a static configuration. It can also be modified on the fly, which is highly flexible for passing arguments. For example

```python
def get_loader(config):
    image_paths = glob.glob(config.path + '*.jpg')
    labels = [line.strip() for line in open(config.path + 'label.txt')]
    # ... do something else
train_data_loader = get_loader(config(path = '../data/train_data/'))
valid_data_loader = get_loader(config(path = '../data/valid_data/'))
```

`jdconfig.Config` provides 4 more methods for specific control when modifying key-value pair on the fly:

- `Config.copy_overwrite`
- `Config.copy_fillup`
- `Config.inplace_overwrite`
- `Config.inplace_fillup`

The methods with `copy` will copy a new `Config` object. The methods with `inplace` will modify in the original `Config` object and then return itself.

The methods with `overwrite` will forcibly overwrite whatever key-value pair in `Config` object. The methods with `fillup` will raise an exception when you try to overwrite an existed key-value pair.

Calling `config(path = '../data/train_data/')` is equivalent to calling `config.copy_overwrite(path = '../data/train_data')`.

### 4.Python-style Comment

Finally, you can comment out some lines in json file just like you comment out code lines in Python. For example, try to modify the json file above:

```json
{
    "dataset": {
        "proc_count": 4,
        "batch_size": 32,
        "image_height": 48,
        "image_width": 1024
    },

    "model": {
        "cnn_channel":  [   128,    128,    256,    256,    256],
        "cnn_kernel" :  [[4, 4], [3, 3], [3, 3], [3, 3], [3, 2]],
        "cnn_stride" :  [[2, 1], [1, 1], [2, 2], [1, 1], [2, 2]],
        "cnn_padding":  [[0, 0], [1, 1], [0, 0], [1, 1], [0, 0]],
        #"dropout": 0.05
        "dropout": 0 
    },

    "init": {
        "name": "normal",
        "args": { "std": 1 }
    },

    "optim": {
        #"name": "Adam",
        #"args": {
        #    "lr": 1e-3,
        #    "betas": [0.9, 0.99]
        #},
        "name": "SGD",
        "args": {
            "lr": 1e-3
        },
        "lr_decay_point": [1000, 2000],
        "clip_grad": null
    },

    "train_iter_count": 100000,
    "report_interval": 10,
    "valid_interval": 10,
    "visualize_interval": 500,
    "visualize_count": 5,
    "save_interval": 1000
}

```

It's not a standard json format, but it can still be loaded by `jdconfig`:

```python
config = Config('hyperparameter.json')
print(config.model.dropout)
print(config.optim)
```

Output:
```shell
0
{'name': 'SGD', 'args': {'lr': 0.001}, 'clip_grad': None, 'lr_decay_point': [1000, 2000]}
```
