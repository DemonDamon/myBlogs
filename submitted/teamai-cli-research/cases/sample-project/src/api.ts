import type { Order } from './types.js';

export interface OrderApiClient {
  fetchOrder(id: string): Promise<Order>;
}

export class HttpOrderApiClient implements OrderApiClient {
  async fetchOrder(id: string): Promise<Order> {
    throw new Error('not implemented');
  }
}
