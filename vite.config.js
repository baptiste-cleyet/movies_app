import { defineConfig } from "vite";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [tailwindcss()],
  build: {
    outDir: "static/dist",
    emptyOutDir: true,
    manifest: true,
    rollupOptions: {
      input: {
        base: "static/js/base.js",
        movie_grid: "static/js/movie_grid.js",
        watchlist: "static/js/watchlist.js",
        movie_detail: "static/js/movie_detail.js",
        style: "static/css/base.css",
      },
    },
  },
});
