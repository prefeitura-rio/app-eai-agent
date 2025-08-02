'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useTheme } from 'next-themes';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { cn } from '@/app/utils/utils';
import { Home, FlaskConical, Settings, PanelLeftClose, PanelRightClose, Moon, Sun, LogOut, Bot, MessageSquare } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/app/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator } from '@/components/ui/dropdown-menu';
import { useSidebar } from '@/app/contexts/SidebarContext';

interface NavItem {
  name: string;
  href: string;
  icon: React.ElementType;
}

interface DisabledNavItem extends NavItem {
  reason: string;
}

const mainNavigation: NavItem[] = [
  { name: 'Início', href: '/', icon: Home },
  { name: 'Experimentos V0', href: '/experiments_v0', icon: FlaskConical },
  { name: 'Experimentos', href: '/experiments', icon: FlaskConical },
  { name: 'Chat EAI', href: '/chat', icon: MessageSquare },
  { name: 'Chat LangGraph', href: '/chat_langgraph', icon: MessageSquare },
  { name: 'Configurações EAI', href: '/eai_settings', icon: Bot },
];

const disabledNavigation: DisabledNavItem[] = [];

export function Sidebar() {
  const pathname = usePathname();
  const { resolvedTheme, setTheme } = useTheme();
  const { token, logout } = useAuth();
  const router = useRouter();
  const [mounted, setMounted] = useState(false);
  const { state, toggle } = useSidebar();
  const isCollapsed = state === 'collapsed';

  useEffect(() => setMounted(true), []);

  const handleLogout = () => {
    logout();
    router.push(`/login?redirect_url=${pathname}`);
  };

  const toggleTheme = () => {
    setTheme(resolvedTheme === 'dark' ? 'light' : 'dark');
  };

  const renderSettings = () => {
    if (!mounted) return null;

    if (isCollapsed) {
        return (
            <DropdownMenu>
                <Tooltip>
                    <TooltipTrigger asChild>
                        <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon" className="h-10 w-10">
                                <Settings className="h-5 w-5" />
                                <span className="sr-only">Configurações</span>
                            </Button>
                        </DropdownMenuTrigger>
                    </TooltipTrigger>
                    <TooltipContent side="right" sideOffset={5}>Configurações</TooltipContent>
                </Tooltip>
                <DropdownMenuContent side="right" align="start" sideOffset={5}>
                    <DropdownMenuItem onClick={toggleTheme}>
                        {resolvedTheme === 'dark' ? <Sun className="mr-2 h-4 w-4" /> : <Moon className="mr-2 h-4 w-4" />}
                        <span>Mudar Tema</span>
                    </DropdownMenuItem>
                    {token && (
                        <>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem onClick={handleLogout} className="text-destructive focus:text-destructive">
                                <LogOut className="mr-2 h-4 w-4" />
                                <span>Sair</span>
                            </DropdownMenuItem>
                        </>
                    )}
                </DropdownMenuContent>
            </DropdownMenu>
        );
    }

    return (
        <Accordion type="single" collapsible className="w-full">
            <AccordionItem value="settings" className="border-none">
                <AccordionTrigger className="flex h-10 w-full items-center justify-start gap-3 rounded-lg px-3 text-xs font-medium text-muted-foreground hover:bg-muted hover:no-underline">
                    <Settings className="h-5 w-5" />
                    <span>Configurações</span>
                </AccordionTrigger>
                <AccordionContent className="pt-1">
                    <div className="flex flex-col gap-1 pl-6">
                        <Button variant="ghost" className="w-full justify-start gap-3 text-xs" onClick={toggleTheme}>
                            {resolvedTheme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
                            <span>Mudar Tema</span>
                        </Button>
                        {token && (
                            <Button variant="ghost" className="w-full justify-start gap-3 text-xs text-destructive hover:text-destructive" onClick={handleLogout}>
                                <LogOut className="h-4 w-4" />
                                <span>Sair</span>
                            </Button>
                        )}
                    </div>
                </AccordionContent>
            </AccordionItem>
        </Accordion>
    );
  }

  return (
    <aside className={cn(
        "hidden flex-col border-r bg-background transition-all duration-300 ease-in-out sm:flex",
        isCollapsed ? "w-16 p-2 items-center" : "w-48 p-2 items-center"
    )}>
        <TooltipProvider delayDuration={100}>
            <nav className="flex h-full flex-col gap-1">
                {/* Top Section */}
                <div className="flex flex-col gap-0">
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <Button variant="ghost" size={isCollapsed ? "icon" : "default"} className={cn("h-10 text-xs", !isCollapsed && "w-full justify-start gap-3 px-3")} onClick={toggle}>
                                {isCollapsed ? <PanelRightClose className="h-5 w-5" /> : <PanelLeftClose className="h-5 w-5" />}
                                {!isCollapsed && <span>Recolher</span>}
                                <span className="sr-only">{isCollapsed ? 'Expandir' : 'Recolher'}</span>
                            </Button>
                        </TooltipTrigger>
                        {isCollapsed && <TooltipContent side="right" sideOffset={5}>{isCollapsed ? 'Expandir' : 'Recolher'}</TooltipContent>}
                    </Tooltip>
                    {renderSettings()}
                </div>

                <div className="my-2 h-px w-full bg-border" />

                {/* Main Navigation */}
                <div className="flex flex-col gap-1">
                    {mainNavigation.map(item => {
                        const isActive = item.href === '/' ? pathname === item.href : pathname.startsWith(item.href);
                        return (
                            <Tooltip key={item.name}>
                                <TooltipTrigger asChild>
                                    <Link href={item.href} className={cn('flex h-10 items-center gap-3 rounded-lg px-3 text-xs font-medium transition-colors', isCollapsed ? 'w-10 justify-center' : 'justify-start', isActive ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:bg-muted hover:text-foreground')}>
                                        <item.icon className="h-5 w-5" />
                                        {!isCollapsed && <span>{item.name}</span>}
                                        <span className="sr-only">{item.name}</span>
                                    </Link>
                                </TooltipTrigger>
                                {isCollapsed && <TooltipContent side="right" sideOffset={5}>{item.name}</TooltipContent>}
                            </Tooltip>
                        );
                    })}
                </div>
                
                <div className="my-2 h-px w-full bg-border" />

                {/* Disabled Navigation */}
                <div className="flex flex-col gap-1">
                    {disabledNavigation.map(item => (
                        <Tooltip key={item.name}>
                            <TooltipTrigger asChild>
                                <div className={cn('flex h-10 items-center gap-3 rounded-lg px-3 text-xs font-medium text-muted-foreground/50 cursor-not-allowed', isCollapsed ? 'w-10 justify-center' : 'justify-start')}>
                                    <item.icon className="h-5 w-5" />
                                    {!isCollapsed && <span>{item.name}</span>}
                                </div>
                            </TooltipTrigger>
                            <TooltipContent side="right" sideOffset={5}>{item.reason}</TooltipContent>
                        </Tooltip>
                    ))}
                </div>
            </nav>
        </TooltipProvider>
    </aside>
  );
}