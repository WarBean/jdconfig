# Designed for highly convenient and flexibly configuring hyperparameters in Deep Learning

## Installation

```shell
# Either
pip install dotconfig
# Or
pip install --upgrade https://github.com/WarBean/dotconfig/tarball/master
```

## Usage

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

Use `dotconfig.Config` to load the configuration:

```python
from dotconfig import Config
config = Config('hyperparameter.json')
print(config.train_iter_count) # 100000
print(config.model.dropout) # 0.05
print(config.model.cnn_channel) # [128, 128, 256, 256, 256] 
```

After that you can pass around the `config` object to wherever it is needed. For example, when I'm using PyTorch to create a network module:

```python
class MyCNN(torch.nn.Sequential):
    def __init__(self, config):
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
            relu = torch.nn.Dropout(config.model.dropout)
            self.add_module('dropout%d' % i, dropout)
            relu = torch.nn.ReLU()
            self.add_module('relu%d' % i, relu)
config = Config('hyperparameter.json')
my_cnn = MyCNN(config)
```

`dotconfig.Config` object is not just a static configuration. It can also be modified on the fly, which is highly flexible for passing arguments. For example

```python
def get_loader(config):
    image_paths = glob.glob(config.path + '*.jpg')
    labels = [line.strip() for line in open(config.path + 'label.txt')]
    # ... do something else
train_data_loader = get_loader(config(path = '../data/train_data/'))
valid_data_loader = get_loader(config(path = '../data/valid_data/'))
```

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

And load it as a `dotconfig.Config` object again:

```python
config = Config('hyperparameter.json')
print(config.model.dropout) # 0
print(config.optim) # {'name': 'SGD', 'args': {'lr': 0.001}, 'clip_grad': None, 'lr_decay_point': [1000, 2000]}
```