import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "个体化情绪诱发视频问卷",
  description: "用于 AI 生成视频的用户画像问卷原型",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
