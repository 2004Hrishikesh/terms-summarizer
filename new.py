import torch
import transformers
from transformers import pipeline

print(torch.__version__)
print(transformers.__version__)

summarizer = pipeline("summarization")
print(summarizer("This is a test sentence for summarization."))