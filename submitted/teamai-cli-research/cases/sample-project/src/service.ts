import { OrderRepository } from './repository.js';
import { HttpOrderApiClient } from './api.js';
import type { Order } from './types.js';

export class OrderService {
  constructor(
    private repo: OrderRepository,
    private client: HttpOrderApiClient,
  ) {}

  async syncOrder(id: string): Promise<Order> {
    const order = await this.client.fetchOrder(id);
    await this.repo.save(order);
    return order;
  }
}
