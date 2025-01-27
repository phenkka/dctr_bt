from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


model_name = "prithivida/parrot_paraphraser_on_T5"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# Функция для перефразирования
def paraphrase_text(text, max_length=4096, num_return_sequences=1):
    input_text = f"paraphrase: {text}"
    input_ids = tokenizer.encode(input_text, return_tensors="pt", truncation=True)

    outputs = model.generate(
        input_ids,
        max_length=max_length,
        num_return_sequences=num_return_sequences,
        num_beams=5,
        early_stopping=True
    )

    # Возвращаем все перефразированные варианты
    return [tokenizer.decode(output, skip_special_tokens=True).strip() for output in outputs]


original_text = "The sun set behind the mountains, painting the sky in shades of orange and pink."
paraphrased_texts = paraphrase_text(original_text)

print("Original:", original_text)
print("Paraphrased:", paraphrased_texts)