declare module 'node:crypto' {
  type DigestEncoding = 'hex' | 'base64url';
  type InputEncoding = 'utf8' | 'ascii';

  interface Hash {
    update(value: string, encoding?: InputEncoding): Hash;
    digest(encoding: DigestEncoding): string;
  }

  export function createHash(algorithm: string): Hash;
  export function randomBytes(size: number): { toString(encoding: 'base64url'): string };
  export function timingSafeEqual(left: Uint8Array, right: Uint8Array): boolean;
}

declare const Buffer: {
  from(value: string, encoding?: 'ascii'): Uint8Array;
};

declare module '@appdeploy/sdk' {
  export type DatabaseRecord<T> = Omit<T, 'id'> & { id: string };

  export const db: {
    add(table: string, records: Array<Record<string, unknown>>): Promise<Array<string | null>>;
    update(
      table: string,
      items: Array<{ id: string; record: Record<string, unknown> }>,
    ): Promise<boolean[]>;
    list<T = Record<string, unknown>>(
      table: string,
      options?: { filter?: Record<string, unknown>; nextToken?: string; limit?: number },
    ): Promise<{ items: Array<DatabaseRecord<T>>; nextToken?: string }>;
    delete(table: string, ids: string[]): Promise<boolean[]>;
  };

  export type RouterResponse = {
    statusCode: number;
    headers: Record<string, string>;
    body: string;
  };

  export function json(data: unknown, status?: number): RouterResponse;
  export function error(message: string, status?: number): RouterResponse;
  export function requireAuth(): (context: unknown) => unknown;
}
