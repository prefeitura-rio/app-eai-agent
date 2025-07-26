// src/frontend/app/components/JsonViewerModal.tsx
'use client';

import React from 'react';
import styles from './JsonViewerModal.module.css';

interface JsonViewerModalProps {
  data: any;
  onClose: () => void;
}

export default function JsonViewerModal({ data, onClose }: JsonViewerModalProps) {
  return (
    <div className={styles.modal_backdrop} onClick={onClose}>
      <div className={styles.modal_content} onClick={e => e.stopPropagation()}>
        <div className={styles.modal_header}>
          <h4 className={styles.modal_title}>JSON Completo</h4>
          <button onClick={onClose} className={styles.close_button}>
            <i className="bi bi-x-lg"></i>
          </button>
        </div>
        <div className={styles.modal_body}>
          <pre>
            <code>{JSON.stringify(data, null, 2)}</code>
          </pre>
        </div>
      </div>
    </div>
  );
}
