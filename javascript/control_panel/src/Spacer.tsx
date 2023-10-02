export const Spacer = ({
  width = 0,
  height = 0
}) => {
  const style:{ width?: string, height?: string } = {};
  if (width) {
    style.width = `${width}px`;
  }
  if (height) {
    style.height = `${height}px`;
  }
  
  return (
    <div className='spacer' style={style} />
  );
};
