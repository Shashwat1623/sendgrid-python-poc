import { Injectable } from '@nestjs/common';
import OpenAI from 'openai';

@Injectable()
export class OpenaiService {
  private client: OpenAI;

  constructor() {
    this.client = new OpenAI({
      apiKey: process.env.OPENAI_KEY, // sk-or-v1-...
      baseURL: 'https://openrouter.ai/api/v1',
      defaultHeaders: {
        'HTTP-Referer': 'https://sendgrid-nest-poc.onrender.com', // can be any valid URL
        'X-Title': 'SendGrid AI Support POC',
      },
    });
  }

  async ask(question: string): Promise<string> {
    const response = await this.client.chat.completions.create({
      model: 'gpt-4o-mini', // cheap + fast for POC
      messages: [
        {
          role: 'system',
          content: 'You are a helpful customer support agent.',
        },
        {
          role: 'user',
          content: question,
        },
      ],
    });

    return response.choices[0].message.content || 'No response';
  }
}
