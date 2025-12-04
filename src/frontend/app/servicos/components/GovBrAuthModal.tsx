'use client';

import { useState } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ShieldCheck, AlertCircle, ExternalLink, Copy, Check } from 'lucide-react';
import { setAccessToken } from '../services/govbr-auth';
import { ADMIN_LOGIN_URL } from '@/app/components/config';

interface GovBrAuthModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export default function GovBrAuthModal({ open, onOpenChange, onSuccess }: GovBrAuthModalProps) {
  const [tokenInput, setTokenInput] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!tokenInput.trim()) {
      setError('Access token e obrigatorio');
      return;
    }

    // Salvar token
    setAccessToken(tokenInput.trim());

    // Sucesso
    onSuccess();
    onOpenChange(false);

    // Limpar formulario
    setTokenInput('');
  };

  const openAdminPage = () => {
    window.open(ADMIN_LOGIN_URL, '_blank', 'noopener,noreferrer');
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(tokenInput);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <ShieldCheck className="h-5 w-5 text-primary" />
            Autenticacao Gov.br
          </DialogTitle>
          <DialogDescription>
            Para acessar o gerenciamento de servicos, faca login com Gov.br e copie o access token.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <Alert className="bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800">
            <AlertCircle className="h-4 w-4 text-blue-600 dark:text-blue-400" />
            <AlertDescription className="text-sm text-blue-900 dark:text-blue-100">
              <div className="space-y-2">
                <p className="font-semibold">Como obter o access token:</p>
                <ol className="list-decimal list-inside space-y-1 ml-2">
                  <li>Clique no botao abaixo para abrir a pagina de login</li>
                  <li>Faca login com seu CPF e senha do Gov.br</li>
                  <li>Apos o login, abra o DevTools (F12)</li>
                  <li>Va em Application &gt; Cookies</li>
                  <li>Procure pelo cookie &quot;access_token&quot;</li>
                  <li>Copie o valor e cole no campo abaixo</li>
                </ol>
              </div>
            </AlertDescription>
          </Alert>

          <Button
            onClick={openAdminPage}
            variant="outline"
            className="w-full"
            type="button"
          >
            <ExternalLink className="mr-2 h-4 w-4" />
            Abrir Pagina de Login ({ADMIN_LOGIN_URL})
          </Button>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="access_token">Access Token</Label>
              <div className="flex gap-2">
                <Input
                  id="access_token"
                  type="text"
                  value={tokenInput}
                  onChange={(e) => setTokenInput(e.target.value)}
                  placeholder="Cole o access token aqui"
                  required
                  className="font-mono text-xs"
                />
                {tokenInput && (
                  <Button
                    type="button"
                    variant="outline"
                    size="icon"
                    onClick={copyToClipboard}
                  >
                    {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                  </Button>
                )}
              </div>
              <p className="text-xs text-muted-foreground">
                O token tem um formato longo (JWT). Exemplo: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
              </p>
            </div>

            {error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <div className="flex justify-end gap-2">
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                Cancelar
              </Button>
              <Button type="submit">
                <ShieldCheck className="mr-2 h-4 w-4" />
                Autenticar
              </Button>
            </div>
          </form>
        </div>
      </DialogContent>
    </Dialog>
  );
}
