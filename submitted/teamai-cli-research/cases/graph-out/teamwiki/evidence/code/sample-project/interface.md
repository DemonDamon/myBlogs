---
title: sample-project interface
domain: code-knowledge
source:
  - src/api.ts
  - src/types.ts
---

# Interface

- `OrderApiClient` ← src/api.ts:3 [EXTRACTED]
  ```
  export interface OrderApiClient {
  ```
- `Order` ← src/types.ts:1 [EXTRACTED]
  ```
  export interface Order {
  ```
- `OrderStatus` ← src/types.ts:8 [EXTRACTED]
  ```
  export type OrderStatus = 'pending' | 'paid' | 'cancelled';
  ```