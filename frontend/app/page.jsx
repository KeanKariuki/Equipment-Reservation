import ResourceCard from "@/components/ResourceCard";
import { getResources } from "@/lib/api";

export default async function HomePage() {
  let resources = [];
  let loadError = null;

  try {
    const data = await getResources();
    resources = data.results ?? data;
  } catch (err) {
    loadError = err.message;
  }

  return (
    <>
      <section className="px-9 pt-14 pb-10 max-w-[600px]">
        <div className="eyebrow mb-3">Equipment &amp; space, by permit</div>
        <h1 className="font-display text-[56px] leading-[0.95] mb-4">
          Book it like you&apos;d
          <br />
          book a trail.
        </h1>
        <p className="text-base text-fm-green-deep/80 leading-relaxed max-w-[44ch] mb-6">
          Pick your gear, pick your window, get a permit. No overlapping bookings, no
          surprises at pickup — just a clean, dated slip that says it&apos;s yours.
        </p>
        <a href="#catalogue" className="btn-outline">
          Browse gear
        </a>
      </section>

      <section id="catalogue" className="px-9 pb-16">
        <h2 className="font-display text-[30px] tracking-wide mb-1">Available at the depot</h2>
        <div className="font-slab text-[13px] text-fm-green-deep/70 mb-6">
          Nairobi &amp; Ruiru yards
        </div>

        {loadError && (
          <p className="text-fm-rust text-sm">
            Couldn&apos;t reach the API ({loadError}). Is the Django server running on{" "}
            <code>NEXT_PUBLIC_API_URL</code>?
          </p>
        )}

        {!loadError && resources.length === 0 && (
          <p className="text-fm-green-deep/70 text-sm">No resources listed yet.</p>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-[18px]">
          {resources.map((resource) => (
            <ResourceCard key={resource.id} resource={resource} />
          ))}
        </div>
      </section>
    </>
  );
}
