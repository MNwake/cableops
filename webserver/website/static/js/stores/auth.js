import { writable } from 'svelte/store';

// Wallet connection state
export const connected = writable(false);
export const account = writable(null);

// Chain/network state
export const chainId = writable(null);
export const networkName = writable('');

// Wallet interface
export const provider = writable(null);
export const signer = writable(null); 