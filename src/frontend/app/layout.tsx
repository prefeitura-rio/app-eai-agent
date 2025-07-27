import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "./contexts/AuthContext";
import { ThemeProvider } from "@/app/components/ThemeProvider";
import { TooltipProvider } from "@/components/ui/tooltip";
import { HeaderProvider } from "./contexts/HeaderContext";
import ConditionalLayout from "./components/ConditionalLayout";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "EAI Admin Panel",
  description: "Admin panel for EAI experiments",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${geistSans.variable} ${geistMono.variable} bg-background text-foreground`}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <TooltipProvider>
            <AuthProvider>
              <HeaderProvider>
                <ConditionalLayout>{children}</ConditionalLayout>
              </HeaderProvider>
            </AuthProvider>
          </TooltipProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
