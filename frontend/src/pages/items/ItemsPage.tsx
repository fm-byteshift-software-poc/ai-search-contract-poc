import { useState } from "react";
import { useItems } from "@/hooks/useItems";
import type { Item, ItemCreate } from "@/types/item";
import { formatCurrency } from "@/utils/format";

const EMPTY_FORM: ItemCreate = { name: "", description: "", price: 0 };

export default function ItemsPage() {
  const { items, loading, error, createItem, deleteItem } = useItems();
  const [form, setForm] = useState<ItemCreate>(EMPTY_FORM);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const handleSubmit = async () => {
    if (!form.name || form.price <= 0) {
      setFormError("Name and a valid price are required.");
      return;
    }
    try {
      setSubmitting(true);
      setFormError(null);
      await createItem(form);
      setForm(EMPTY_FORM);
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "Failed to create item");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (item: Item) => {
    if (!confirm(`Delete "${item.name}"?`)) return;
    await deleteItem(item.id);
  };

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold text-base-content">Items</h1>

      {/* Create Form */}
      <div className="card bg-base-200 shadow">
        <div className="card-body">
          <h2 className="card-title">New Item</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <input
              type="text"
              placeholder="Name"
              className="input input-bordered w-full"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
            <input
              type="text"
              placeholder="Description (optional)"
              className="input input-bordered w-full"
              value={form.description ?? ""}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
            />
            <input
              type="number"
              placeholder="Price"
              className="input input-bordered w-full"
              value={form.price}
              min={0}
              onChange={(e) =>
                setForm({ ...form, price: parseFloat(e.target.value) || 0 })
              }
            />
          </div>
          {formError && (
            <p className="text-error text-sm mt-1">{formError}</p>
          )}
          <div className="card-actions justify-end mt-2">
            <button
              className="btn btn-primary"
              onClick={handleSubmit}
              disabled={submitting}
            >
              {submitting ? (
                <span className="loading loading-spinner loading-sm" />
              ) : (
                "Create"
              )}
            </button>
          </div>
        </div>
      </div>

      {/* List */}
      {loading ? (
        <div className="flex justify-center py-12">
          <span className="loading loading-spinner loading-lg text-primary" />
        </div>
      ) : error ? (
        <div className="alert alert-error">
          <span>{error}</span>
        </div>
      ) : items.length === 0 ? (
        <div className="text-center text-base-content/50 py-12">
          No items yet. Create one above.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="table table-zebra w-full">
            <thead>
              <tr>
                <th>Name</th>
                <th>Description</th>
                <th>Price</th>
                <th>Created</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id}>
                  <td className="font-medium">{item.name}</td>
                  <td className="text-base-content/60">
                    {item.description ?? "—"}
                  </td>
                  <td>{formatCurrency(item.price)}</td>
                  <td className="text-base-content/60 text-sm">
                    {new Date(item.created_at).toLocaleDateString()}
                  </td>
                  <td>
                    <button
                      className="btn btn-ghost btn-sm text-error"
                      onClick={() => handleDelete(item)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
