# API Architecture Overview


## To run
Run make up on the backend-coding-interview directory.    Had claude throw some other commands in there for adding migrations, linting, etc.

## Foundation & Setup
I chose Django REST Framework (DRF) for its efficient viewset-based approach to API development. The setup includes drf-spectacular for Swagger documentation, providing an intuitive interface for API testing and exploration. The entire application is containerized using Docker for consistent deployment.

## Authentication Strategy
JWT token authentication secures write operations (PUT, PATCH, DELETE endpoints). Read operations (GET) remain publicly accessible to facilitate easy sharing—appropriate for the use case of this exercise. An admin role is provisioned automatically on startup using environment variables. While suitable for this prototype, a production implementation would require a more robust user management system.

## Data Models

### Picture Model
- **photo_id**: Source-provided identifier, currently configured as a unique numeric field. For multi-source support, this would become a non-unique string field.
- **width/height**: Stored for potential aspect ratio calculations and display optimizations.
- **url**: Complete resource URL for reference purposes.
- **src_url**: Direct image URL serving as the base for size variations.
- **avg_color**: Available for UI theming or design purposes.
- **alt**: Descriptive text doubling as the picture name.
- **created_at/updated_at**: Standard audit timestamps.

**Design Decision**: Eliminated storage of multiple size-specific URLs. Since these follow a predictable pattern (src_url + size parameters), the serializer dynamically generates them. This could alternatively be handled client-side, but I've implemented as model properties for convenience on certain endpoints—particularly single-picture detail views.

### Photographer Model
A separate model manages photographer data (URL, name, ID) since multiple pictures can share the same photographer. The system uses `get_or_create` logic matching both ID and name when associating pictures with photographers.

**Rationale for dual matching**: While IDs alone could serve as unique identifiers, using both ID and name provides flexibility for future multi-source integration where IDs might conflict across platforms.

### Source Model (Not Implemented)
Multi-source support would require substantial architectural changes:
- Many-to-many relationships between photographers and sources
- Complex ID namespace management
- Modified lookup strategies for photographer-picture associations

The current single-source design intentionally avoids this complexity.

## API Endpoints (Viewsets)
Viewsets provide rapid endpoint scaffolding with intelligent data expansion based on context:
- **Photographer list**: Returns photo counts only
- **Photographer detail**: Includes summary information for each associated photo
- **Photo detail**: Returns comprehensive photo data including size variations

For creation of images, for the api request I had the photographer be a nested object of the picture.  Its a better organization of it.

**Future Enhancement**: 

- Implement query parameters (e.g., `photo-details=true`) to allow clients to request expanded data at the list level when needed.

- Bulk adds for pictures:  Right now it just ingest one at a time but if i had a list of pictures I want to do it in as few calls as possible.  The best way to do that is to extract all of the information on the photographer first in case any of the pictures share a photographer, then create the photographs as well.  Since its bulk you would want to do it as get_or_create for the pictures as well since you dont want it to just fail if one picture was already uploaded.

- 

## Admin Interface
The admin panel provides basic management capabilities:
- Photographers display with photo counts
- Photos can be reassigned to different photographers
- Deliberately minimal to maintain simplicity

## URL Configuration
Three primary URL groups:
- Django admin interface
- Swagger/OpenAPI documentation endpoints
- Photo API routes

## Testing
I focused on model creation and the views for the test.  Models test was to make sure they are created correctly, viewsets make sure it comes back on api calls and checks some of the serializers as well, and if it is authenticated vs not.

I try to avoid testing DJANGO itself.  I've been on teams where testing basic django functionality is done.  