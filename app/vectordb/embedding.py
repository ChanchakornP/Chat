# from transformers import AutoModel, AutoTokenizer

# tokenizer = AutoTokenizer.from_pretrained("facebook/contriever")
# model = AutoModel.from_pretrained("facebook/contriever")


# def mean_pooling(token_embeddings, mask):
#     token_embeddings = token_embeddings.masked_fill(~mask[..., None].bool(), 0.0)
#     sentence_embeddings = token_embeddings.sum(dim=1) / mask.sum(dim=1)[..., None]
#     return sentence_embeddings


# def embed(sentences):
#     # Apply tokenizer
#     inputs = tokenizer(sentences, padding=True, truncation=True, return_tensors="pt")

#     # Compute token embeddings
#     outputs = model(**inputs)

#     embeddings = mean_pooling(outputs[0], inputs["attention_mask"])
#     return embeddings
