from torch.utils.data import DataLoader, Subset
from torchvision import datasets, transforms
import torch


def getOxfordPetsDataloaders(config):
    # Define transforms
    test_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    train_transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.RandomCrop((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(brightness=0.25, contrast=0.25, saturation=0.25, hue=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    # Load the full dataset without transforms
    full_dataset = datasets.OxfordIIITPet(
        root='./datasets/data',
        split='trainval',
        download=True
    )

    # Split into train and validation sets
    indices = torch.randperm(len(full_dataset))
    val_size = len(full_dataset) // 8
    train_set = Subset(full_dataset, indices[:-val_size])
    val_set = Subset(full_dataset, indices[-val_size:])

    # Load the test set without transforms
    test_set = datasets.OxfordIIITPet(
        root='./datasets/data',
        split='test',
        download=True
    )

    # Create dataloaders with transforms applied at the loader level
    train_loader = DataLoader(
        train_set, 
        shuffle=True, 
        batch_size=config["bs"], 
        num_workers=config["num_workers"], 
        pin_memory=True, 
        prefetch_factor=2,
        collate_fn=lambda batch: (torch.stack([train_transform(img) for img, _ in batch]), 
                                 torch.tensor([label for _, label in batch]))
    )
    
    val_loader = DataLoader(
        val_set, 
        shuffle=False, 
        batch_size=5*config["bs"], 
        num_workers=config["num_workers"], 
        pin_memory=True, 
        prefetch_factor=2,
        collate_fn=lambda batch: (torch.stack([test_transform(img) for img, _ in batch]), 
                                 torch.tensor([label for _, label in batch]))
    )
    
    test_loader = DataLoader(
        test_set, 
        shuffle=False, 
        batch_size=config["bs"],
        collate_fn=lambda batch: (torch.stack([test_transform(img) for img, _ in batch]), 
                                 torch.tensor([label for _, label in batch]))
    )

    return train_loader, val_loader, test_loader
