export interface Order {
  id: string;
  userId: string;
  amount: number;
  status: OrderStatus;
}

export type OrderStatus = 'pending' | 'paid' | 'cancelled';
