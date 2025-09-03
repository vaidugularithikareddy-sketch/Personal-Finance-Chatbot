
export enum Sender {
  User = 'user',
  Bot = 'bot',
}

export interface Message {
  id: string;
  text: string;
  sender: Sender;
}

export enum UserType {
  Student = 'student',
  Professional = 'professional',
}
