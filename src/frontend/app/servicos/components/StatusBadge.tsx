import { Badge } from '@/components/ui/badge';

interface StatusBadgeProps {
  status: 0 | 1;
}

export default function StatusBadge({ status }: StatusBadgeProps) {
  if (status === 1) {
    return (
      <Badge variant="default" className="bg-green-600 hover:bg-green-700">
        Publicado
      </Badge>
    );
  }

  return (
    <Badge variant="secondary" className="bg-yellow-600 hover:bg-yellow-700 text-white">
      Rascunho
    </Badge>
  );
}
