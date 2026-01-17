import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Combine class names with tailwind-merge
 * @param {...(string|object|array)} inputs - Class names to merge
 * @returns {string} Merged class names
 */
export function cn(...inputs) {
  return twMerge(clsx(inputs));
}
