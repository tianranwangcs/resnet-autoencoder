import torch
from torch import nn
from autoencoder import ResNet_autoencoder, Bottleneck, DeconvBottleneck
from coco import load_dataset

if __name__ == "__main__":
    model = ResNet_autoencoder(Bottleneck, DeconvBottleneck, [
        3, 4, 6, 3], 3).cuda()

    # load data
    dataloader = load_dataset('G:\\example')

    '''
    load pre_trained_model
    '''
    pretrained_dict = torch.load("G:\\resnet50-19c8e357.pth")
    model_dict = model.state_dict()
    # 1. filter out unnecessary keys
    pretrained_dict = {k: v for k,
                       v in pretrained_dict.items() if k in model_dict}
    # 2. overwrite entries in the existing state dict
    model_dict.update(pretrained_dict)
    model.load_state_dict(model_dict)

    # fix encoder
    fix_length = len(pretrained_dict.keys())
    all_length = len(model.state_dict().keys())
    for idx, k in enumerate(model_dict.keys()):
        if idx < fix_length:
            model.state_dict()[k].requires_grad = False

    params = filter(lambda p: p.requires_grad, model.parameters())

    # Loss and Optimizer
    criterion = nn.MSELoss()

    optimizer = torch.optim.Adam(params, lr=0.001)

    model.train()
    for batch_idx, (image, target) in enumerate(dataloader):
        image = image.cuda()

        # Forward + Backward + Optimize

        optimizer.zero_grad()

        tmp1, tmp2, tmp3 = model(image)

        loss = criterion(image, tmp2) + criterion(tmp1, tmp3)

        loss.backward()

        optimizer.step()
