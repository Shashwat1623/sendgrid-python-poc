import { Injectable } from '@nestjs/common';

const sgMail = require('@sendgrid/mail');

@Injectable()
export class SendgridService {
  constructor() {
    if (!process.env.SENDGRID_KEY) {
      console.error('❌ SENDGRID_KEY not set');
    }
    sgMail.setApiKey(process.env.SENDGRID_KEY);
  }

  async sendAcknowledgement(to: string, aiReply: string) {
  const msg = {
    to,
    from: process.env.FROM_EMAIL,
    subject: 'Re: Your support request',
    text: aiReply,
    html: `<p>${aiReply.replace(/\n/g, '<br/>')}</p>`,
  };

  const res = await sgMail.send(msg);
  console.log('✅ SendGrid response:', res[0].statusCode);
}

}
