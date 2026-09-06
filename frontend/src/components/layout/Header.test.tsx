import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { Header } from './Header'

describe('Header connection status', () => {
  it('shows independently healthy backend, API, and AI states', () => {
    render(<Header backend api ai ws="disconnected" lastUpdated={null} />)
    expect(screen.getByText(/backend online/i)).toBeInTheDocument()
    expect(screen.getByText(/api online/i)).toBeInTheDocument()
    expect(screen.getByText(/ai ready/i)).toBeInTheDocument()
  })

  it('does not mark health services offline when only live monitoring is disconnected', () => {
    render(<Header backend api ai ws="disconnected" lastUpdated={null} />)
    expect(screen.getByText(/live disconnected/i)).toBeInTheDocument()
    expect(screen.queryByText(/backend offline/i)).not.toBeInTheDocument()
    expect(screen.queryByText(/api offline/i)).not.toBeInTheDocument()
  })
})
