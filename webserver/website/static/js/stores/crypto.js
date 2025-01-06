import { writable } from 'svelte/store';

// Available tokens for swapping
export const availableTokens = writable([]);

export const fetchAvailableTokens = async () => {
    try {
        const response = await fetch('/api/crypto/top-tokens');
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const tokens = await response.json();
        console.log('Updated tokens:', tokens);
        availableTokens.set(tokens);
    } catch (error) {
        console.error('Error fetching tokens:', error);
    }
}; 