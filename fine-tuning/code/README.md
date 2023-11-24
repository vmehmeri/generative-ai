# Code Fine-tuning
Here you'll find:

* **Code_LLM_Fine_Tuning_Dataset_Generation_and_Augmentation_with_PaLM_API.ipynb**: Notebook for generating a well-formatted fine-tuning dataset (JSONL) from a Google Sheet file containing two columns (input, output). It also contains utility code for augmenting the dataset using Google Cloud's text LLM (PaLM 2) and for creating and launching a fine-tuning pipeline.
* **augmented_fine_tuning_dataset.jsonl**: The generated augmented dataset (notebook output) which you can use directly in a fine-tuning pipeline
* **finetuning_dataset.csv**: A sample fine-tuning dataset of 100 examples (this is a CSV export from Google Sheet)
