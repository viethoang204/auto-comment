import openai

def run_openai_chat(content,num_account):
    openai.api_key = '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'
    # messages = [{"role": "system", "content": "You are an intelligent assistant. Only answer in Vietnamese. Just answer what I ask, nothing more or explain more or sentence that not related to the answare."}]
    messages = [{"role": "system", "content": "Please respond only in Vietnamese with concise, direct answers, avoiding unnecessary explanations or filler phrases like 'here you are' or 'below is your answer'"}]

    message = f'dưới góc nhìn của người đọc báo, hãy liệt kê ra {num_account} câu bình luận ngắn và tự nhiên về đoạn văn dưới đây, có icon cảm xúc ở cuối mỗi câu: "{content}"'
    if message:
        messages.append(
            {"role": "user", "content": message},
        )
        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages
        )
    reply = chat.choices[0].message.content
    return reply
