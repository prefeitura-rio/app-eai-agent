import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Separator } from '@/components/ui/separator';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { RefreshCw, Lock, Unlock, Copy, History, Loader2, MessageSquare, Eraser, Trash2, Clock } from 'lucide-react';
import { HistoryMessage } from '../../services/api';

interface ChatSidebarProps {
  userNumber: string;
  setUserNumber: (value: string) => void;
  isNumberFixed: boolean;
  isMounted: boolean;
  provider: string;
  reasoningEngineId: string;
  setReasoningEngineId: (value: string) => void;
  sessionTimeoutSeconds: number;
  setSessionTimeoutSeconds: (value: number) => void;
  useWhatsappFormat: boolean;
  setUseWhatsappFormat: (value: boolean) => void;
  isLoadingHistory: boolean;
  isDeletingHistory: boolean;
  historyMessages: HistoryMessage[];
  historyError: string | null;
  showDeleteModal: boolean;
  setShowDeleteModal: (value: boolean) => void;
  
  // Handlers
  onGenerateNumber: () => void;
  onToggleFixNumber: () => void;
  onCopyNumber: () => void;
  onLoadHistory: () => void;
  onClearScreen: () => void;
  onDeleteHistory: () => void;
}

const ChatSidebar: React.FC<ChatSidebarProps> = ({
  userNumber,
  setUserNumber,
  isNumberFixed,
  isMounted,
  provider,
  reasoningEngineId,
  setReasoningEngineId,
  sessionTimeoutSeconds,
  setSessionTimeoutSeconds,
  useWhatsappFormat,
  setUseWhatsappFormat,
  isLoadingHistory,
  isDeletingHistory,
  historyMessages,
  historyError,
  showDeleteModal,
  setShowDeleteModal,
  onGenerateNumber,
  onToggleFixNumber,
  onCopyNumber,
  onLoadHistory,
  onClearScreen,
  onDeleteHistory,
}) => {
  return (
    <Card className="flex flex-col h-full">
      <CardHeader>
        <CardTitle>Parâmetros</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 overflow-y-auto space-y-4">
        <div className="space-y-2">
          <Label htmlFor="user-number">User Number</Label>
          <div className="flex items-center space-x-2">
            <Input
              id="user-number"
              value={isMounted ? userNumber : ''}
              onChange={(e) => !isNumberFixed && setUserNumber(e.target.value)}
              disabled={isNumberFixed}
              className="flex-1"
            />
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button 
                    variant="outline" 
                    size="icon" 
                    onClick={onGenerateNumber}
                    disabled={isNumberFixed || !isMounted}
                  >
                    <RefreshCw className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Gerar novo número aleatório</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button 
                    variant="outline" 
                    size="icon" 
                    onClick={onToggleFixNumber}
                    disabled={!isMounted}
                  >
                    {isNumberFixed ? <Lock className="h-4 w-4" /> : <Unlock className="h-4 w-4" />}
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>{isNumberFixed ? "Desbloquear número" : "Fixar número"}</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button 
                    variant="outline" 
                    size="icon" 
                    onClick={onCopyNumber}
                    disabled={!isMounted}
                  >
                    <Copy className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Copiar número</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="provider">Provider</Label>
          <Input
            id="provider"
            value={provider}
            disabled
            className="bg-muted"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="reasoning-engine-id">Reasoning Engine ID</Label>
          <Input
            id="reasoning-engine-id"
            value={reasoningEngineId}
            onChange={(e) => setReasoningEngineId(e.target.value)}
            placeholder="reasoning_engine_id (opcional)"
          />

        </div>

        <Separator className="my-4" />

        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <History className="h-4 w-4 text-primary" />
            <h3 className="font-semibold text-sm">Histórico</h3>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="session-timeout">Session Timeout (segundos)</Label>
            <Input
              id="session-timeout"
              type="number"
              value={sessionTimeoutSeconds}
              onChange={(e) => setSessionTimeoutSeconds(parseInt(e.target.value) || 3600)}
              min="60"
              max="86400"
              placeholder="3600"
            />
            <p className="text-xs text-muted-foreground">
              Tempo limite para agrupar mensagens na mesma sessão
            </p>
          </div>

          <div className="flex items-center space-x-2">
            <Checkbox
              id="whatsapp-format"
              checked={useWhatsappFormat}
              onCheckedChange={(checked) => setUseWhatsappFormat(checked as boolean)}
            />
            <Label htmlFor="whatsapp-format" className="text-sm">
              Formato WhatsApp
            </Label>
          </div>

          <div className="space-y-2">
            <Button
              onClick={onLoadHistory}
              disabled={isLoadingHistory || !isMounted}
              className="w-full"
              variant="outline"
            >
              {isLoadingHistory ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Carregando...
                </>
              ) : (
                <>
                  <MessageSquare className="h-4 w-4 mr-2" />
                  Carregar Histórico
                </>
              )}
            </Button>

            <Button
              onClick={onClearScreen}
              disabled={!isMounted}
              className="w-full"
              variant="outline"
            >
              <Eraser className="h-4 w-4 mr-2" />
              Limpar Tela
            </Button>

            <Dialog open={showDeleteModal} onOpenChange={setShowDeleteModal}>
              <DialogTrigger asChild>
                <Button
                  disabled={isDeletingHistory || isLoadingHistory || !isMounted}
                  className="w-full"
                  variant="destructive"
                >
                  {isDeletingHistory ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Deletando...
                    </>
                  ) : (
                    <>
                      <Trash2 className="h-4 w-4 mr-2" />
                      Deletar Histórico
                    </>
                  )}
                </Button>
              </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
              <DialogHeader>
                <DialogTitle className="flex items-center gap-2 text-destructive">
                  <Trash2 className="h-5 w-5" />
                  Deletar Histórico
                </DialogTitle>
                <DialogDescription className="text-base">
                  Tem certeza que deseja deletar <strong>PERMANENTEMENTE</strong> todo o histórico do usuário <code className="bg-muted px-1 py-0.5 rounded text-sm font-mono">{userNumber}</code>?
                </DialogDescription>
              </DialogHeader>
              
              <div className="py-4">
                <div className="flex items-start gap-3 p-4 bg-destructive/10 border border-destructive/20 rounded-lg">
                  <div className="text-destructive mt-0.5">⚠️</div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-destructive mb-1">Atenção!</h4>
                    <ul className="text-sm text-destructive/80 space-y-1">
                      <li>• Esta ação não pode ser desfeita</li>
                      <li>• Todos os checkpoints serão removidos</li>
                      <li>• O histórico será perdido permanentemente</li>
                    </ul>
                  </div>
                </div>
              </div>

              <DialogFooter className="gap-2">
                <Button
                  variant="outline"
                  onClick={() => setShowDeleteModal(false)}
                  disabled={isDeletingHistory}
                >
                  Cancelar
                </Button>
                <Button
                  variant="destructive"
                  onClick={onDeleteHistory}
                  disabled={isDeletingHistory}
                >
                  {isDeletingHistory ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Deletando...
                    </>
                  ) : (
                    <>
                      <Trash2 className="h-4 w-4 mr-2" />
                      Sim, Deletar
                    </>
                  )}
                </Button>
              </DialogFooter>
            </DialogContent>
            </Dialog>
          </div>

          {historyError && (
            <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-md">
              <p className="text-sm text-destructive">{historyError}</p>
            </div>
          )}

          {historyMessages.length > 0 && (
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-green-600" />
                <span className="text-sm font-medium text-green-600">
                  {historyMessages.filter(m => m.message_type !== 'usage_statistics').length} mensagens carregadas
                </span>
              </div>
              <Button
                onClick={onClearScreen}
                size="sm"
                variant="ghost"
                className="h-6 px-2 text-xs"
              >
                Limpar Tudo
              </Button>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default ChatSidebar;
