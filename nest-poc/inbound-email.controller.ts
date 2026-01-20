import {
  Controller,
  Post,
  UploadedFiles,
  UseInterceptors,
  Body,
} from '@nestjs/common';
import { AnyFilesInterceptor } from '@nestjs/platform-express';
import { diskStorage } from 'multer';
import { extname } from 'path';
import { SendgridService } from '../sendgrid/sendgrid.service';
import { OpenaiService } from 'src/openai.service';

@Controller()
export class InboundEmailController {
  constructor(
    private readonly sendgrid: SendgridService,
    private readonly openai: OpenaiService,
  ) {}


  @Post('inbound-email')
  @UseInterceptors(
    AnyFilesInterceptor({
      storage: diskStorage({
        destination: '/tmp/uploads', // IMPORTANT for Render
        filename: (req, file, cb) => {
          const unique = Date.now() + '-' + Math.round(Math.random() * 1e9);
          cb(null, unique + extname(file.originalname));
        },
      }),
    }),
  )
  async receiveEmail(
    @Body() body: any,
    @UploadedFiles() files: Array<Express.Multer.File>,
  ) {
    console.log('📩 New Email Received');

    const { from, to, subject, text } = body;

    console.log('From:', from);
    console.log('Subject:', subject);

    // Extract email from "Name <email>"
    const senderEmail = from?.match(/<(.+)>/)?.[1] || from;

    // ✅ Send acknowledgement
    const question = body.text || body.subject;

    console.log('🧠 Asking AI:', question);

    const aiReply = await this.openai.ask(question);

    console.log('🤖 AI reply:', aiReply);

    await this.sendgrid.sendAcknowledgement(senderEmail, aiReply);

    return 'OK';
  }
}
