export const FlexContainer = ({
  flexDirection = 'initial',
  justifyContent = 'initial',
  alignItems = 'initial',
  className = '',
  children = null
}:{
  flexDirection?:string,
  justifyContent?:string,
  alignItems?:string,
  className?:string,
  children?:any
}) => (
  <div
    className={`flex_container ${className}`}
    style={{
      display: 'flex',
      flexDirection: flexDirection,
      justifyContent,
      alignItems,
    } as React.CSSProperties}
  >
    {children}
  </div>
);
