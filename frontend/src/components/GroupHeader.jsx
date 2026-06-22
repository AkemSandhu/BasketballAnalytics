import { useState } from 'react'

const GroupHeader = (props) => {
  const [isOpen, setIsOpen] = useState(true)
  const { displayName, childColIds } = props.params
  const api = props.api  // AG Grid API passed automatically

  const toggleGroup = () => {
    const newState = !isOpen
    setIsOpen(newState)
    // Toggle visibility of child columns (the representative column stays)
    childColIds.forEach(colId => {
      api.setColumnsVisible([colId], newState)
    })
  }

  return (
    <div style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }} onClick={toggleGroup}>
      <span style={{ marginRight: 8, fontSize: 12 }}>
        {isOpen ? '▼' : '►'}
      </span>
      <span style={{ fontWeight: 'bold' }}>{displayName}</span>
    </div>
  )
}

export default GroupHeader