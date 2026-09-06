import { render,screen } from '@testing-library/react';import { describe,expect,it } from 'vitest';import { StatusBadge } from './StatusBadge'
describe('StatusBadge',()=>{it('includes the textual status for non-color communication',()=>{render(<StatusBadge label="CRITICAL" tone="CRITICAL"/>);expect(screen.getByText('CRITICAL')).toBeInTheDocument()})})
