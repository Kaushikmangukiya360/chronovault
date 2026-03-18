# gRPC Integration

> Built by **@kaushik mangukiya**  
> Found a bug or have feedback? → kaushikmangukiya360@gmail.com

gRPC mode is intended for typed, low-latency service-to-service integration.

Recommended flow:

1. Define protobuf service methods for CRUD/query operations.
2. Validate bearer token metadata at interceptor layer.
3. Forward scoped calls to chronovault vault instance.
4. Return JSON-serializable protobuf messages.

```bash
pip install chronovault[grpc]
```

---
<div align="center">

**chronovault** — Enterprise Encrypted JSON Database for Python

Built with love by [@kaushik mangukiya](https://github.com/kaushikmangukiya360)  
Bug reports & feedback → kaushikmangukiya360@gmail.com

</div>
