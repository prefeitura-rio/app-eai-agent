'use client';

import React from 'react';
import Link from 'next/link';
import styles from './AppHeader.module.css';

interface ActionButton {
  id: string;
  label: string;
  icon: string;
  href?: string;
  onClick?: () => void;
  variant?: 'default' | 'logout';
}

interface AppHeaderProps {
  title: string;
  subtitle?: string;
  actions: ActionButton[];
}

export default function AppHeader({ title, subtitle, actions }: AppHeaderProps) {
  return (
    <header className={styles.header}>
      <div className={styles.header_content}>
        <div className={styles.title_section}>
          <h1 className={styles.title}>{title}</h1>
          {subtitle && <small className={styles.dataset_name}>{subtitle}</small>}
        </div>
        <div className={styles.actions_section}>
          {actions.map(action => {
            const buttonClass = action.variant === 'logout' ? styles.logout_btn : styles.action_btn;
            
            if (action.href) {
              return (
                <Link key={action.id} href={action.href} className={buttonClass} title={action.label}>
                  <i className={`bi ${action.icon}`}></i>
                </Link>
              );
            }
            
            return (
              <button key={action.id} onClick={action.onClick} className={buttonClass} title={action.label}>
                <i className={`bi ${action.icon}`}></i>
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
}
