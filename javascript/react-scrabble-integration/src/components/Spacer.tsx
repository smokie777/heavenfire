import { memo } from 'react'

export const Spacer = memo(
  ({ height = 0, width = 0 }:{ height?:number|string, width?:number|string }) => (
    <div style={{ height, width }} />
  )
);
