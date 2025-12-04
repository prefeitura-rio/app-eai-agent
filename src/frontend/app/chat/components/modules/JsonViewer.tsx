import React from 'react';

const JsonViewer = ({ data }: { data: object }) => (
  <pre className="p-2 bg-muted/50 rounded-md text-base-custom whitespace-pre-wrap break-all font-mono">
    {JSON.stringify(data, null, 2)}
  </pre>
);

export default JsonViewer;
