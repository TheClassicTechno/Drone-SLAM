import './Skeleton.css'

export function DeliverySkeleton() {
  return (
    <>
      {[1, 2, 3].map((i) => (
        <div key={i} className="skeleton-delivery">
          <div className="skeleton skeleton-delivery-icon"></div>
          <div className="skeleton-delivery-content">
            <div className="skeleton skeleton-delivery-title"></div>
            <div className="skeleton skeleton-delivery-status"></div>
          </div>
        </div>
      ))}
    </>
  )
}

export function ActivitySkeleton() {
  return (
    <>
      {[1, 2, 3, 4].map((i) => (
        <div key={i} className="skeleton-activity">
          <div className="skeleton-activity-header">
            <div className="skeleton skeleton-activity-name"></div>
            <div className="skeleton skeleton-activity-time"></div>
          </div>
          <div className="skeleton skeleton-activity-text"></div>
          {i % 2 === 0 && (
            <div className="skeleton skeleton-activity-text short"></div>
          )}
        </div>
      ))}
    </>
  )
}
