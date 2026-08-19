import type { Order } from './types.js';

export class OrderRepository {
  async save(order: Order): Promise<void> {
    // persist to db
  }
  async findById(id: string): Promise<Order | null> {
    return null;
  }
}
