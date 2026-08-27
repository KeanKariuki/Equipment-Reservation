import BookingForm from "@/components/BookingForm";
import { getResource } from "@/lib/api";

export default async function ResourceDetailPage({ params }) {
  const { id } = await params;
  const resource = await getResource(id);

  return (
    <section className="px-9 py-12 grid grid-cols-1 lg:grid-cols-[1.2fr_0.8fr] gap-10">
      <div>
        {resource.image_url && (
          <div className="aspect-[16/10] border-2 border-fm-green-deep overflow-hidden mb-6">
            <img
              src={resource.image_url}
              alt={resource.name}
              className="w-full h-full object-cover"
            />
          </div>
        )}
        <span className="inline-block font-slab text-[11px] font-semibold uppercase tracking-wide text-fm-rust border border-fm-rust px-[9px] py-[3px] mb-4">
          {resource.resource_type} · {resource.category}
        </span>
        <h1 className="font-display text-[42px] leading-none mb-4">{resource.name}</h1>
        <p className="text-base text-fm-green-deep/80 leading-relaxed max-w-[52ch]">
          {resource.description}
        </p>
      </div>

      <BookingForm resource={resource} />
    </section>
  );
}