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
  centerTitle?: boolean;
}

export default function AppHeader({ title, subtitle, actions, centerTitle = false }: AppHeaderProps) {
  const getButtonClass = (action: ActionButton) => {
    switch (action.id) {
      case 'home':
        return styles.home_btn;
      case 'back':
        return styles.back_btn;
      case 'refresh':
        return styles.refresh_btn;
      case 'theme':
        return styles.theme_btn;
      case 'logout':
        return styles.logout_btn;
      default:
        return styles.action_btn;
    }
  };

  const titleSectionClass = `${styles.title_section} ${centerTitle ? styles.title_section_center : ''}`;

  return (
    <header className={styles.header}>
      <div className={styles.header_content}>
        <div className={titleSectionClass}>
          <h1 className={styles.title}>{title}</h1>
          {subtitle && <small className={styles.dataset_name}>{subtitle}</small>}
        </div>
        <div className={styles.actions_section}>
          {actions.map(action => {
            const buttonClass = getButtonClass(action);
            
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
