import { defineConfig } from "umi";

export default defineConfig({
  plugins: ['@umijs/plugins/dist/antd'],
  antd:{
    configProvider: {
      
    },
    theme: {
      token: {
        borderRadius: 0
      }
    }
  },
  routes: [
    { path: "/", component: "home" },
    { path: "/faces", component: "faces" },
    { path: "/image", component: "image" },
    { path: "/video", component: "video" },
    { path: "/camera", component: "camera" },
  ],
  npmClient: 'yarn',
  define: {
    'process.env.API_ADDR': 'http://localhost:8100'
  }
});
