import Link from "next/link";

const UNIT_LABEL = { hour: "/hr", day: "/day" };

export default function ResourceCard({ resource }) {
  return (
    <Link
      href={`/resources/${resource.id}`}
      className="block bg-white border-2 border-fm-green-deep hover:-translate-y-0.5 transition-transform"
    >
      <div className="aspect-[4/3] border-b-2 border-fm-green-deep overflow-hidden bg-fm-green-deep/5">
        {resource.image_url ? (
          <img
            src={resource.image_url}
            alt={resource.name}
            className="w-full h-full object-cover"
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-[11px] font-slab uppercase tracking-wide text-fm-green-deep/40">
            No photo
          </div>
        )}
      </div>

      <div className="p-[18px]">
      <span className="inline-block font-slab text-[11px] font-semibold uppercase tracking-wide text-fm-rust border border-fm-rust px-[9px] py-[3px] mb-3">
        {resource.resource_type}
      </span>
      <h4 className="font-display text-[21px] leading-none mb-1.5">{resource.name}</h4>
      <div className="text-[13px] text-fm-green-deep/70 mb-4">{resource.location || resource.category}</div>
      <div className="flex justify-between items-baseline border-t border-fm-line pt-3">
        <span className="text-xs text-fm-green-deep/70">
          Deposit calculated at checkout
        </span>
        <b className="font-display text-[19px]">
          KES {Number(resource.price).toLocaleString()}
          {UNIT_LABEL[resource.pricing_unit] || ""}
        </b>
      </div>
      </div>
    </Link>
  );
}
