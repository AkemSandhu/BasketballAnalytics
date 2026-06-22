import { useState } from 'react'

const PlayerProfileViewer = ({ selectedRows, onClose }) => {
  const [activeTab, setActiveTab] = useState(0)
  const tabs = ['Overview', 'Shooting', 'Advanced', 'Badges', 'Similar'] // placeholders for future

  // If multiple rows, show a grid of profiles
  const isMulti = selectedRows.length > 1

  return (
    <div className="fixed inset-0 bg-black/80 z-50 flex justify-center items-center p-4">
      <div className="bg-surface rounded-xl w-full max-w-6xl max-h-[90vh] overflow-y-auto p-6 border border-border relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-textSecondary hover:text-textPrimary text-2xl"
        >
          &times;
        </button>

        {isMulti ? (
          // Grid view for multiple players
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {selectedRows.map((row, idx) => (
              <div key={idx} className="bg-surfaceLight p-4 rounded-lg border border-border">
                <ProfileHeader row={row} />
                {/* Placeholder for future details */}
                <div className="mt-2 text-textSecondary text-sm">Tab: {tabs[activeTab]}</div>
                <div className="mt-2 h-20 bg-surface rounded flex items-center justify-center text-textSecondary">
                  Coming soon
                </div>
              </div>
            ))}
          </div>
        ) : (
          // Single profile view with tabs
          <div>
            <ProfileHeader row={selectedRows[0]} />
            <div className="flex space-x-2 mt-4 border-b border-border pb-2">
              {tabs.map((tab, idx) => (
                <button
                  key={idx}
                  onClick={() => setActiveTab(idx)}
                  className={`px-4 py-2 rounded-t-lg transition-colors ${
                    activeTab === idx
                      ? 'bg-primary text-white'
                      : 'bg-surfaceLight text-textSecondary hover:bg-border'
                  }`}
                >
                  {tab}
                </button>
              ))}
            </div>
            <div className="mt-4 p-4 bg-surfaceLight rounded-lg min-h-32 flex items-center justify-center text-textSecondary">
              Tab content for "{tabs[activeTab]}" will go here
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

const ProfileHeader = ({ row }) => (
  <div>
    <h2 className="text-xl font-bold text-textPrimary">{row.player_name}</h2>
    <div className="grid grid-cols-2 gap-1 text-sm text-textSecondary mt-1">
      <span>Season: {row.season}</span>
      <span>Age: {row.age}</span>
      <span>Off. Role: {row.offensive_role}</span>
      <span>Def. Role: {row.defensive_role}</span>
      <span>Minutes: {row.mp}</span>
    </div>
  </div>
)

export default PlayerProfileViewer